# imgproxy-lite

A quick a dirty realtime image converter for use in kubernetes.

I use hugo for my blog.  I like to dump the images for this blog onto ceph object storage to keep them out of the hugo pods.  This proxy allows me to do so care-free with regard to file size; as images can now be referenced from hugo like so:

```
![](https://images.example/?img=worms.jpg&q=33)
```

This is a technique often used in ecommerce; for example images hosted on media.sweetwater.com are served with an open-ended `?quality=` parameter.

For now this service is hard-coded to go look for the source images on a ceph RGW gateway.

Are we adding a point of failure vs pre-processing and storing a handful of 'presets'?  Yes, but running this as a replicated deployment, with a CluserIP and Ingress, on the same cluster as the ceph RGW pods and Service; I consider this very low risk and easily worth the ease and flexibility of content organization going forward.

Heres a terraform deployment:

```
resource "kubernetes_ingress_v1" "imgproxy-lite" {
  metadata {
    name = "imgproxy-lite"
    annotations = {
      "kubernetes.io/ingress.class"    = "nginx"
      "cert-manager.io/cluster-issuer" = "letsencrypt-prod"
    }
  }
  spec {
    rule {
      host = "images.nih.earth"
      http {
        path {
          backend {
            service {
              name = "imgproxy-lite"
              port {
                number = 5000
              }
            }
          }
          path      = "/"
          path_type = "Prefix"
        }
      }
    }
    tls {
      hosts       = ["images.nih.earth"]
      secret_name = "imgproxy-lite-tls"
    }
  }
}

resource "kubernetes_service" "imgproxy-lite" {
  metadata {
    name = "imgproxy-lite"
  }
  spec {
    selector = {
      app = "imgproxy-lite"
    }
    port {
      port        = "5000"
      target_port = "5000"
    }
    type = "ClusterIP"
  }
}

resource "kubernetes_deployment" "imgproxy-lite" {
  metadata {
    name = "imgproxy-lite"
  }
  spec {
    replicas = 5
    selector {
      match_labels = {
        app = "imgproxy-lite"
      }
    }
    template {
      metadata {
        labels = {
          app = "imgproxy-lite"
        }
      }
      spec {
        container {
          image = "images.local:5000/imgproxy-lite"
          name  = "imgproxy-lite"
        }
      }
    }
  }
}
```
