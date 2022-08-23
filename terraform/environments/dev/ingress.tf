module "cert_manager" {
  source = "terraform-iaac/cert-manager/kubernetes"

  cluster_issuer_email                   = var.cert_issuer_email
  cluster_issuer_name                    = "letsencrypt"
  cluster_issuer_private_key_secret_name = "cert-manager-private-key"
}

resource "kubernetes_namespace" "ingress_nginx" {
  metadata {
    name = "ingress-nginx"
  }
}

module "nginx-controller" {
  source    = "terraform-iaac/nginx-controller/helm"
  version   = "2.0.2"
  namespace = "ingress-nginx"
  # TODO: does this require cert_manager up and running or can they be completed in parallel
  depends_on = [
    module.cert_manager, resource.kubernetes_namespace.ingress_nginx
  ]
}

resource "kubectl_manifest" "ingress" {
  yaml_body = <<YAML
kind: Ingress
apiVersion: networking.k8s.io/v1
metadata:
  name: nginx-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/clusterissuer: "letsencrypt"
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-methods: "PUT, GET, POST, OPTIONS, DELETE"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://${var.web_app_domain},http://localhost:4200,https://_CKT_DOMAIN"
    nginx.ingress.kubernetes.io/cors-allow-credentials: "true"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
spec:
  tls:
    - hosts:
      - ${var.api_domain}
      secretName: autodocprocessing # [TODO] Change this to anything
  defaultBackend:
    service:
      name: adp-ui
      port:
        number: 80
  rules:
  - host: ${var.api_domain}
    http:
      paths:
      - path: /upload_service/v1
        pathType: Prefix
        backend:
          service:
            name: upload-service
            port:
              number: 80
      - path: /classification_service/v1
        pathType: Prefix
        backend:
          service:
            name: classification-service
            port:
              number: 80
      - path: /validation_service/v1
        pathType: Prefix
        backend:
          service:
            name: validation-service
            port:
              number: 80
      - path: /extraction_service/v1
        pathType: Prefix
        backend:
          service:
            name: extraction-service
            port:
              number: 80
      - path: /hitl_service/v1
        pathType: Prefix
        backend:
          service:
            name: hitl-service
            port:
              number: 80
      - path: /document_status_service/v1
        pathType: Prefix
        backend:
          service:
            name: document-status-service
            port:
              number: 80
      - path: /matching_service/v1
        pathType: Prefix
        backend:
          service:
            name: matching-service
            port:
              number: 80

YAML

  depends_on = [
    module.nginx-controller
  ]

}
