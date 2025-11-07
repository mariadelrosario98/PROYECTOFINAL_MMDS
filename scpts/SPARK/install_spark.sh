# --- 1. INSTALACIÓN DE PREREQUISITOS (Adaptado para Amazon Linux 2) ---
sudo yum update -y
sudo yum install java-17-amazon-corretto wget python3-pip -y

# --- 2. DESCARGAR Y DESCOMPRIMIR SPARK ---
# Variables (ya están en el script, pero las definimos aquí por claridad)
SPARK_VERSION="spark-3.5.1"
HADOOP_VERSION="bin-hadoop3"
SPARK_TAR="${SPARK_VERSION}-${HADOOP_VERSION}.tgz"
SPARK_URL="https://dlcdn.apache.org/spark/spark-3.5.1/${SPARK_TAR}"
INSTALL_DIR="/opt"

wget -q ${SPARK_URL} -P /tmp/
sudo tar -xzf /tmp/${SPARK_TAR} -C ${INSTALL_DIR}
sudo mv ${INSTALL_DIR}/${SPARK_VERSION}-${HADOOP_VERSION} ${INSTALL_DIR}/spark

# --- 3. CONFIGURAR VARIABLES DE ENTORNO (Haciendo el script ejecutable) ---
# Añadir SPARK_HOME y JAVA_HOME
echo 'export SPARK_HOME="/opt/spark"' | sudo tee -a /etc/profile
echo 'export PATH="$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin"' | sudo tee -a /etc/profile
# Obtener JAVA_HOME para Amazon Corretto
JAVA_HOME_PATH=$(dirname $(dirname $(readlink -f /usr/bin/java)))
echo "export JAVA_HOME=${JAVA_HOME_PATH}" | sudo tee -a /etc/profile

# Aplicar las variables de entorno inmediatamente en tu sesión
source /etc/profile

# --- 4. INSTALAR PYSPARK EN TU AMBIENTE VIRTUAL ACTIVO ---
# **Importante:** Asume que ya ejecutaste 'source spark_env/bin/activate'
pip install pyspark

# --- 5. INICIAR EL MAESTRO DE SPARK (OPCIONAL) ---
# Ejecutar con sudo para que tenga permisos en /opt/spark/logs
sudo /opt/spark/sbin/start-master.sh