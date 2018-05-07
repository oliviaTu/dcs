######## Dockerfile来源
FROM registry.sviyun.com/os/svi-centos6:v1.5
######## 编写Dockerfiler人员邮箱
MAINTAINER tumin <1536918570@qq.com>

######## 网元相关变量
ENV APP_HOME /opt/powercloud/dcs
ENV APP_NAME dcs_server

######## 自定义变量，没有可以不用写
ENV JETTY_HOME ${APP_HOME}/${APP_NAME}/jetty9
ENV JETTY_RUN ${JETTY_HOME}/bin

######## 定义服务等待依赖
#   1、支持协议(file, tcp, tcp4, tcp6, http, https and unix)
#   3、变量值必须包含协议类型，服务域名，端口
#   2、实例说明：表示当前Dockerfile启动需要依赖数据库和authcenter的web服务。
#ENV APP_DEP1 "tcp://mysql-lb.mysql:3306"
#ENV APP_DEP2 "http://web.authcenter:80"

######## 以下内容无需编辑修改
ADD *.tar.gz /tmp
RUN cd /tmp/*_release && \
    cp -f docker/*.sh /usr/local/bin/ && \
    chmod a+x /usr/local/bin/*.sh && \
    cp -r docker/conf /usr/local/conf && \
    touch /var/log/${APP_NAME}.log && \
    # setup app
    sh setup.sh && \
    cd ~ && \
    rm -rf /tmp/*_release

WORKDIR ${APP_HOME}/${APP_NAME}

ENTRYPOINT ["tini", "--"]

CMD ["start.sh"]





