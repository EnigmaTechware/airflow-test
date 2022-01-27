#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
This is an example dag for using a Kubernetes Executor Configuration.
"""
import logging
import os
from datetime import datetime

from airflow import DAG
from airflow.configuration import conf
from airflow.decorators import task
from airflow.example_dags.libs.helper import print_stuff

log = logging.getLogger(__name__)

worker_container_repository = conf.get('kubernetes', 'worker_container_repository')
worker_container_tag = conf.get('kubernetes', 'worker_container_tag')

try:
    from kubernetes.client import models as k8s
except ImportError:
    log.warning(
        "The example_kubernetes_executor example DAG requires the kubernetes provider."
        " Please install it with: pip install apache-airflow[cncf.kubernetes]"
    )
    k8s = None

if k8s:
    with DAG(
        dag_id='simple_kubernetes_executor',
        schedule_interval=None,
        start_date=datetime(2021, 1, 1),
        catchup=False,
        tags=['yescnc'],
    ) as dag:
        # You can use annotations on your kubernetes pods!
        start_task_executor_config = {
            "pod_override": k8s.V1Pod(metadata=k8s.V1ObjectMeta(annotations={"test": "annotation"}))
        }

        @task(executor_config=start_task_executor_config)
        def start_task():
            print_stuff()

        start_task = start_task()

        # [START task_with_volume]
        executor_config_volume_mount = {
            "pod_override": k8s.V1Pod(
                spec=k8s.V1PodSpec(
                    containers=[
                        k8s.V1Container(
                            name="base",
                            volume_mounts=[
                                k8s.V1VolumeMount(mount_path="/foo/", name="example-kubernetes-test-volume")
                            ],
                        )
                    ],
                    volumes=[
                        k8s.V1Volume(
                            name="example-kubernetes-test-volume",
                            host_path=k8s.V1HostPathVolumeSource(path="/tmp/"),
                        )
                    ],
                )
            ),
        }

        @task(executor_config=executor_config_volume_mount)
        def test_volume_mount():
            """
            Tests whether the volume has been mounted.
            """

            with open('/foo/volume_mount_test.txt', 'w') as foo:
                foo.write('Hello')

            return_code = os.system("cat /foo/volume_mount_test.txt")
            if return_code != 0:
                raise ValueError(f"Error when checking volume mount. Return code {return_code}")

        volume_task = test_volume_mount()
        # [END task_with_volume]

#        start_task >> [volume_task, other_ns_task, sidecar_task] >> third_task >> [base_image_task, four_task]
        start_task >> volume_task
