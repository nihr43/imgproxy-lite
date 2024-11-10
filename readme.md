# imgproxy-lite

A quick and dirty realtime image converter for use in kubernetes.

I use hugo for my blog.  I like to dump the images for this blog onto ceph object storage to keep them out of the hugo pods.  This proxy allows me to do so care-free with regard to file size; as images can now be referenced from hugo like so:

```
![](https://images.example/?img=worms.jpg&q=33)
```

This is a technique often used in ecommerce; for example images hosted on media.sweetwater.com are served with an open-ended `?quality=` parameter.

For now this service is hard-coded to go look for the source images on a ceph RGW gateway.

Are we adding a point of failure vs pre-processing and storing a handful of 'presets'?  Yes, but running this as a replicated deployment, with a CluserIP and Ingress, on the same cluster as the ceph RGW pods and Service; I consider this very low risk and easily worth the ease and flexibility of content organization going forward.

Heres a terraform deployment with objects cached on ceph:

```
resource "kubernetes_service" "imgproxy-lite" {
  depends_on = [kubernetes_deployment.imgproxy-lite]
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
  depends_on = [kubernetes_persistent_volume_claim.imgproxy-lite]
  metadata {
    name = "imgproxy-lite"
  }
  spec {
    replicas = 2
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
          env {
            name  = "PYTHONUNBUFFERED"
            value = "1"
          }
          volume_mount {
            mount_path = "/opt/artifacts"
            name       = "scratch"
          }
        }
        volume {
          name = "scratch"
          persistent_volume_claim {
            claim_name = "imgproxy-lite"
          }
        }
      }
    }
  }
}

resource "kubernetes_persistent_volume_claim" "imgproxy-lite" {
  metadata {
    name = "imgproxy-lite"
  }
  spec {
    access_modes = ["ReadWriteMany"]
    resources {
      requests = {
        storage = "1Gi"
      }
    }
    storage_class_name = "ceph-filesystem"
  }

```
