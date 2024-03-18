from qiniu import Auth, put_data
from AeroIntelligenceDjango import settings
def uploadFile(key,file): #key是文件名,file是要上传的文件
    access_key = settings.ACCESS_KEY
    secret_key = settings.SECRET_KEY
    # order_id = request.data.get('order_id')
    # key = request.data.get('order_id') + '.jpg'
    # # key=上传到七牛云的文件名
    # file = request.data.get('file')
    # # 获取前端传来的文件对象
    q = Auth(access_key, secret_key)
    # 通过密钥生成一个对象
    bucket_name = settings.BUCKET_NAME
    # 获取配置的空间地址名称
    token = q.upload_token(bucket_name, key, 3600)
    # 生成token
    ret, info = put_data(token, key, file)
    # 传送文件到七牛云，file是文件对象本身
    if info.status_code == 200:
        return "http://rzyi06q9n.hb-bkt.clouddn.com/"+key
    else:
        return 400