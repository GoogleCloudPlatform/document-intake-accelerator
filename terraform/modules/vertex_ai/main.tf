/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

# Copying sample model to GCS bucket.
resource "null_resource" "upload_ml_model" {
  provisioner "local-exec" {
    command = "gsutil cp -r ../../../sample_data/classification_model gs://${var.model_gcs_path}/classification_model"
  }
}

# Import Vertex AI model.
resource "null_resource" "import_vertex_ai_model" {
  depends_on = [
    null_resource.upload_ml_model,
  ]

  provisioner "local-exec" {
    command = join(" ", [
      "gcloud ai models upload",
      "--region=${var.region}",
      "--display-name=${var.model_name}",
      "--container-image-uri=${var.image_uri}",
      "--artifact-uri=${var.model_gcs_path}/classification_model",
    ])
  }
}

# Create endpoint
resource "null_resource" "create_vertex_ai_endpoint" {
  depends_on = [
    null_resource.import_vertex_ai_model,
  ]

  provisioner "local-exec" {
    command = join(" ", [
      "gcloud ai endpoints create",
      "--region=${var.region}",
      "--display-name=${var.model_name}-endpoint",
    ])
  }
}

data "external" "model" {
  depends_on = [
    null_resource.import_vertex_ai_model,
  ]
  program = [
    "python",
    "../../modules/vertex_ai/get_gcloud_value.py",
  ]
  query = {
    query_type   = "models"
    display_name = "${var.model_name}"
    region       = var.region
  }
}

data "external" "endpoint" {
  depends_on = [
    null_resource.create_vertex_ai_endpoint,
  ]
  program = [
    "python",
    "../../modules/vertex_ai/get_gcloud_value.py",
  ]
  query = {
    query_type   = "endpoints"
    display_name = "${var.model_name}-endpoint"
    region       = var.region
  }
}

output "output" {
  value = {
    model_id    = data.external.model.result.name
    endpoint_id = data.external.endpoint.result.name
  }
}

# Deploy model to endpoint
resource "null_resource" "deploy_model_to_endpoint" {
  depends_on = [
    null_resource.create_vertex_ai_endpoint,
    null_resource.import_vertex_ai_model,
    data.external.endpoint,
    data.external.model,
  ]

  provisioner "local-exec" {
    command = join(" ", [
      "gcloud ai endpoints deploy-model ${data.external.endpoint.result.name}",
      "--model=${data.external.model.result.name}",
      "--region=${var.region}",
      "--display-name=${var.model_name}-endpoint",
      "${var.accelerator_param}",
    ])
  }
}
