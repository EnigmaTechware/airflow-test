# -*- coding: utf-8 -*-
import datetime

from airflow import models
from airflow.kubernetes.secret import Secret
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
# from utils.kubernetes import Tolerations, Affinity

YESTERDAY = datetime.datetime.now() - datetime.timedelta(days=1)


with models.DAG(
        dag_id='composer_kubernetes_pod_simple',
        schedule_interval=timedelta(hours=1),
        start_date=YESTERDAY,
        tags=['yescnc-new'],
    ) as dag:
    kubernetes_min_pod = KubernetesPodOperator(
        task_id='pod-workshop-simple',
        name='pod-workshop-simple',
        cmds=['echo', '"Hello world"'],
        namespace='default',
        resources={'request_memory': '128Mi',
                   'request_cpu': '500m',
                   'limit_memory': '500Mi',
                   'limit_cpu': 1},
        image='ubuntu:latest',
        # tolerations=Tolerations.default,
        # affinity=Affinity.memory_heavy,
    )
