# imgproxy-lite

A quick and dirty realtime image converter for use in kubernetes.

I use hugo for my blog.  I like to dump the images for this blog onto ceph object storage to keep them out of the hugo pods.  This proxy allows me to do so care-free with regard to file size; as images can now be referenced from hugo like so:

```
![](https://images.example/?img=worms.jpg&q=33)
```

This is a technique often used in ecommerce; for example images hosted on media.sweetwater.com are served with an open-ended `?quality=` parameter.

For now this service is hard-coded to go look for the source images on a ceph RGW gateway.

Are we adding a point of failure - as opposed to a pre-processed 'presets' approach?  Sure, but running this as a replicated deployment on physically the same cluster as ceph; I consider this very low risk and easily worth the ease and flexibility of content organization going forward.

Heres an argocd deployment with objects cached on ceph.  `imgproxy-lite-gc` [garbage collects the cache directory](https://signal.nih.earth/posts/imgproxy_gc/):

```
---
apiVersion: v1
kind: Service
metadata:
  name: imgproxy-lite
  namespace: default
spec:
  selector:
    app: imgproxy-lite
  ports:
    - port: 5000
      targetPort: 5000
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: imgproxy-lite
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: imgproxy-lite
  template:
    metadata:
      labels:
        app: imgproxy-lite
    spec:
      containers:
        - name: imgproxy-lite
          image: images.local:5000/imgproxy-lite
          command: ["python3", "app.py", "--serve"]
          env:
            - name: PYTHONUNBUFFERED
              value: "1"
          volumeMounts:
            - mountPath: /opt/artifacts
              name: scratch
      volumes:
        - name: scratch
          persistentVolumeClaim:
            claimName: imgproxy-lite
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: imgproxy-lite-gc
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: imgproxy-lite-gc
  template:
    metadata:
      labels:
        app: imgproxy-lite-gc
    spec:
      containers:
        - name: imgproxy-lite-gc
          image: images.local:5000/imgproxy-lite
          command: ["python3", "app.py", "--gc"]
          env:
            - name: PYTHONUNBUFFERED
              value: "1"
          volumeMounts:
            - mountPath: /opt/artifacts
              name: scratch
      volumes:
        - name: scratch
          persistentVolumeClaim:
            claimName: imgproxy-lite
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: imgproxy-lite
  namespace: default
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
  storageClassName: ceph-filesystem
```
