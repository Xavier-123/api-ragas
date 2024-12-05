# 获取镜像

```shell
# 在公司网络环境
docker push harbor.inspur.local/system/ragas:v0.2.6-torch2.5.1-cu122-py311
```



docker-compose.yaml

```yaml
services:

  ragas-service:
    container_name: ragas-service
    image: harbor.inspur.local/system/ragas:v0.2.6-torch2.5.1-cu122-py311
    ports:
      - 18121:8018                 # 端口映射
    environment:
      NVIDIA_VISIBLE_DEVICES: 0    # 指定使用GPU编号，可不用GPU
      OPENAI_API_KEY: None
    working_dir: /api-ragas
    networks:
      - ragas-service-network
    entrypoint: ["python3", "main.py"]

networks:
  ragas-service-network:
    driver: bridge
```



# 启动程序

```
# 在docker-compose.yaml路径下执行
# 清理容器
docker-compose down

# 后台启动
docker-compose up -d

# 查看日志
docker-compose logs -f 
```

