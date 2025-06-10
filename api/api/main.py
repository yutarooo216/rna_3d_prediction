import json
import base64
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from kubernetes import client, config

# FastAPIアプリケーションの初期化
app = FastAPI()

# フロントとの連携
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Reactの開発URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kubernetesクライアントの設定
try:
    config.load_incluster_config()  # クラスター内で実行する場合
except Exception as e:
    raise Exception(f"Failed to load Kubernetes config: {e}")

# Kubernetes Batch APIクライアント
batch_v1 = client.BatchV1Api()

# リクエストボディのスキーマ
class RNARequest(BaseModel):
    sequence: str  # RNA配列
    email: EmailStr  # ユーザーのメールアドレス

# RNA配列を含むJSONを作成する関数
def create_input_json(sequence, job_name):
    """
    Create the input JSON for a single RNA sequence
    """
    input_json = [{
        "sequences": [
            {
                "rnaSequence": {
                    "sequence": sequence,
                    "count": 1,
                    "modifications": []
                }
            }
        ],
        "name": job_name,
        "covalent_bonds": []
    }]
    return input_json

# RNA配列を処理するJobを作成
def create_rna_processing_job(rna_sequence: str, email: str):
    # Job名を動的に生成
    job_name = f"rna-processing-job-{uuid.uuid4().hex[:8]}"

    # input JSONを作成
    input_json_dict = create_input_json(rna_sequence, job_name)
    json_str = json.dumps(input_json_dict)
    json_base64 = base64.b64encode(json_str.encode()).decode()

    # meta.jsonの作成
    meta_data = {job_name: email}
    meta_json_str = json.dumps(meta_data)
    meta_json_base64 = base64.b64encode(meta_json_str.encode()).decode()

    # コンテナの設定
    container = client.V1Container(
        name="rna-processor",
        image="980921727789.dkr.ecr.ap-northeast-1.amazonaws.com/gpu-repository:v1.0",
        command=["sh", "-c"],
        args=[
            f"""
            cd /app/Proteinx && \
            echo '{json_base64}' | base64 -d > examples/example.json && \
            protenix predict --input examples/example.json --out_dir ./output/{job_name} --seeds 101 && \
            cd ./output && \
            echo '{meta_json_base64}' | base64 -d > {job_name}/{job_name}.json && \
            zip /tmp/{job_name}.zip {job_name}/{job_name}/seed_101/predictions/* -j && \
            mv /tmp/{job_name}.zip ./{job_name} && \
            rm -rf {job_name}/{job_name}
            """
        ],
        resources=client.V1ResourceRequirements(
            limits={"nvidia.com/gpu": "1"}
        ),
        volume_mounts=[
            client.V1VolumeMount(
                name="checkpoint-volume",
                mount_path="/app/Proteinx/release_data/checkpoint"
            ),
            client.V1VolumeMount(
                name="components-volume",
                mount_path="/af3-dev/release_data"
            ),
            client.V1VolumeMount(
                name="kubeconfig-volume",
                mount_path="/root/.kube",
                read_only=True
            ),
            client.V1VolumeMount(
                name="output-volume", 
                mount_path="/app/Proteinx/output"
            ),
            client.V1VolumeMount(  # /dev/shm のマウントを追加
                name="dshm",
                mount_path="/dev/shm"
            )
        ]
    )

    # Podテンプレートの設定
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "rna-processor"}),
        spec=client.V1PodSpec(
            containers=[container],
            restart_policy="Never",
            node_selector={"node-type": "gpu"},
            tolerations=[
                client.V1Toleration(
                    key="nvidia.com/gpu",
                    operator="Equal",
                    value="present",
                    effect="NoSchedule"
                )
            ],
            service_account_name="cluster-role",
            volumes=[
                client.V1Volume(
                    name="checkpoint-volume",
                    persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                        claim_name="pvc-checkpoint"
                    )
                ),
                client.V1Volume(
                    name="components-volume",
                    persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                        claim_name="pvc-components"
                    )
                ),
                client.V1Volume(
                    name="output-volume",
                    persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                        claim_name="pvc-output"
                    )
                ),
                client.V1Volume(
                    name="kubeconfig-volume",
                    host_path=client.V1HostPathVolumeSource(
                        path="/home/user1/.kube"
                    )
                ),
                client.V1Volume(  # shared memory 用 emptyDir
                    name="dshm",
                    empty_dir=client.V1EmptyDirVolumeSource(
                        medium="Memory"
                    )
                )
            ]
        )
    )

    # Jobの設定
    job_spec = client.V1JobSpec(
        template=template,
        backoff_limit=1,
        ttl_seconds_after_finished=60
    )

    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_name),
        spec=job_spec
    )

    # KubernetesにJobを作成
    try:
        batch_v1.create_namespaced_job(namespace="my-app", body=job)
        return {"message": f"RNA processing Job {job_name} submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create RNA Job: {str(e)}")

# ヘルスチェックエンドポイント
@app.get("/")
async def health_check():
    return {"status": "ok"}

# RNA配列を受け取ってHelmセットアップとJobを作成するエンドポイント
@app.post("/submit-job/")
def submit_job(request: RNARequest):
    email=request.email
    # RNA処理用のJobを作成
    return create_rna_processing_job(rna_sequence=request.sequence, email=request.email)