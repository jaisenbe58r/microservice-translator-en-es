# Microservicio Deep-Learning alojado en DigitalOcean usando Docker, Flask y Nginx

![Portada](images/Portada1.PNG)

El objetivo de este articulo es desplegar una aplicación de Flask utilizando Docker, con el objetivo de crear un microservicio alojado en un Droplet de DigitalOcean como servidor, con acceso al microservicio bajo un dominio personal con nuestro droplet.

Queremos que uWSGI funcione como servidor web y queremos que el tráfico se enrute a través de Nginx. Estas dos piezas tienen sus propias dependencias, propósito y responsabilidades, por lo que podemos aislar cada una en un contenedor. Por lo tanto, podemos construir dos Dockerfiles para cada servicio, que ```docker-compose``` luego los ejecutaran, montarán volúmenes y configurarán hosts para que ambos puedan comunicarse entre sí.

La aplicación a desplegar como microservicio va a ser el Traductor Inglés-Español basado en Transformers que se implementó en el [post anterior](https://medium.com/@jaimesendraberenguer/transformer-para-la-traducci%C3%B3n-de-texto-91c6d57d375d)




## Introducción

**Docker** es una aplicación de código abierto que permite crear, administrar, implementar y replicar aplicaciones usando contenedores. Los contenedores pueden considerarse como un paquete que alberga solo las dependencias requeridas por la aplicación para ejecutarse a nivel de sistema operativo. Esto significa que cada aplicación implementada con Docker tienen un entorno propio y sus requisitos se gestionan por separado.

**Flask** es un micromarco web que se compila con Python. Se denomina micromarco porque no requiere herramientas ni complementos específicos para ejecutarse. El marco de Flask es ligero y flexible, pero muy estructurado. Esto lo convierte en la opción preferida por encima de otros marcos.

Implementar una aplicación de Flask con Docker le permitirá replicarla en varios servidores con una reconfiguración mínima.

A través de este tutorial, creará una aplicación de Flask y la implementará con Docker.


## Requisitos previos

Para completar este tutorial, necesitará lo siguiente:

- Droplet en DigitalOcean, puede basarse en el siguiente [tutorial.](https://www.digitalocean.com/docs/droplets/how-to/create/)
- Un usuario no root con privilegios sudo configurados siguiendo la [guía Configuración inicial para servidores con Ubuntu 18.04.](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-18-04)
- Un servidor de Ubuntu 18.04 con Docker instalado, configurado siguiendo este [tutorial.](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04)
- Docker instalado en su servidor, configurado siguiendo este [tutorial.](https://www.digitalocean.com/community/tutorials/como-instalar-y-usar-docker-en-ubuntu-18-04-1-es)
- Nginx instalado siguiendo el paso uno del tutorial [Cómo instalar Nginx en Ubuntu 18.04.](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04)
- Lectura y comprensión sobre el artículo [TRANSFORMER para la Traducción de Texto.](https://medium.com/@jaimesendraberenguer/transformer-para-la-traducci%C3%B3n-de-texto-91c6d57d375d)


## Entorno de desarrollo

Antes que nada vamos a necesitar preparar el entorno de desarrollo para la implementación de la aplicación. Para ello primero procedemos a clonar el [repositorio de GitHub](https://github.com/jaisenbe58r/microservice-translator-en-es) base en su servidor, donde os he dejado preparado todo el código necesario para el desarrollo de esta práctica.

```python
cd you_proyect
git clone 
```

## Paso 1: Configurar la aplicación de Flask

El directorio ```microservice-translator-en-es``` contendrá todos los archivos relacionados con la aplicación de Flask, como sus vistas y modelos. Las vistas son el código para responder a las solicitudes a su aplicación. Los modelos crean componentes de aplicaciones, y admiten patrones comunes dentro de una aplicación y entre varias de estas.

El directorio ```static``` es el punto en el que se alojan recursos como los archivos de imagen, CSS y JavaScript. El directorio ```templates``` es el espacio en el que dispondrá las plantillas HTML para su proyecto. El directorio ```model```será donde se guardarán los checkpoints de los modelos entrenados del Transformer.

El archivo ```__init__.py``` dentro del directorio ```app```, indica al intérprete de Python que el directorio ```app``` es un paquete y debería tratarse como tal. ```__init__.py``` creará una instancia de Flask e importará la lógica desde el archivo ```views.py```:

```python
from flask import Flask
app = Flask(__name__)

from app import views
```

El archivo ```app.py``` del directorio app contendrá la mayor parte de la lógica de la aplicación.

```python
@app.route('/')
@app.route('/index')
def index():
    return flask.render_template('index.html')

@app.route('/result', methods = ['POST'])
def result():
    if request.method == 'POST':
        to_predict_list = request.form.to_dict()
        to_predict_list = list(to_predict_list.values())
        try:
            to_predict_list = list(map(str, to_predict_list))
            result = ValuePredictor(to_predict_list)
            prediction=f'es: {result}'
        except ValueError:
            prediction='Error en el formato de los datos'

        sentence=f'en: {to_predict_list[0]}'
        return render_template("result.html", sentence=sentence, prediction=prediction)
```

La línea ```@app.route``` sobre la función se conoce como decorador. Los decoradores modifican la función que los sigue. En este caso, el decorador indica a Flask la URL que desencadenará la función ```index()```. Esta función renderizará el ```index.html``` en el momento que el servidor reciba una petición ```GET``` a ```/``` o ```index```.


El archivo ```uwsgi.ini``` contendrá las configuraciones de uWSGI para nuestra aplicación. uWSGI es una opción de implementación para Nginx que es tanto un protocolo como un servidor de aplicaciones. El servidor de aplicaciones puede proporcionar los protocolos uWSGI, FastCGI y HTTP.

```python
[uwsgi]
module = main
callable = app
master = true
```

Este código define el módulo desde el que se proporcionará la aplicación de Flask, en este caso es el archivo ```main.py```. La opción _callable_ indica a uWSGI que use la instancia de app exportada por la aplicación principal. La opción master permite que su aplicación siga ejecutándose, de modo que haya poco tiempo de inactividad incluso cuando se vuelva a cargar toda la aplicación.

el archivo ```main.py``` contiene lo siguiente:

```python
from app import app
```

Finalmente, el archivo requirements.txt especifica las dependencias que el administrador de paquetes pip instalará en la implementación de Docker:

```python
Flask==1.0.2
tensorflow==2.1.0
mlearner==0.2.3
```

## Paso 2: Configurar Docker

Para crear su implementación de Docker se necesitan dos archivos, dos archivos, Dockerfile y start.sh. El archivo Dockerfile es un documento de texto que contiene los comandos utilizados para ensamblar la imagen. El archivo start.sh es una secuencia de comandos shell que creará una imagen y un contenedor desde Dockerfile.

```Dockerfile``` estos comandos especifican la forma en que se creará la imagen y los requisitos adicionales que se incluirán.

```Dockerfile
FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7

RUN apk --update add bash nano

ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static

COPY ./requirements.txt /var/www/requirements.txt

RUN pip install -r /var/www/requirements.txt
```


En este ejemplo, la imagen de Docker se creará a partir de una imagen existente, ```tiangolo/uwsgi-nginx-flask```, que podrá encontrar en [DockerHub.](https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask)

Las primeras dos líneas especifican la imagen principal que utilizará para ejecutar la aplicación e instalar el procesador de comandos bash y el editor de texto _nano_. También instala el cliente git para realizar extracciones desde servicios de alojamiento de control de versiones, como GitHub, GitLab y Bitbucket, e incorporaciones en ellos. ```ENV STATIC_URL /static``` es una variable de entorno específica para esta imagen de Docker. Define la carpeta estática desde la cual se proporcionan todos los recursos como imágenes, archivos CSS y archivos JavaScript.

Las últimas dos líneas copiarán el archivo ```requirements.txt``` al contenedor para que pueda ejecutarse y luego analice el archivo ```requirements.txt``` para instalar las dependencias especificadas.

Antes de escribir la secuencia de ```comandos start.sh```, primero asegúrese de disponer de un puerto abierto para usarlo en la configuración. Para verificar si hay un puerto libre, ejecute el siguiente comando:

```shell
sudo nc localhost 56733 < /dev/null; echo $?
```

Si el resultado del comando anterior es ```1```, el puerto estará libre y podrá utilizarse. De lo contrario, deberá seleccionar un puerto diferente para usarlo en su archivo de configuración ```start.sh```.

La secuencia de comandos ```start.sh``` es una secuencia de comandos de shell que creará una imagen desde Dockerfile y un contenedor a partir de la imagen de Docker resultante:

```shell
app="docker.test"
docker build -t ${app} .
docker run -d -p 56733:80 \
  --name=${app} \
  -v $PWD:/app ${app}
```

La primera línea se denomina _shebang_. Especifica que este es un archivo bash y se ejecutará como comandos. En la siguiente línea se especifica el nombre que desea dar a la imagen y al contenedor, y se guarda como una app con nombre variable. La siguiente línea indica a Docker que cree una imagen desde su Dockerfile ubicado en el directorio actual. Con esto, se creará una imagen llamada docker.translate en este ejemplo.

Con las últimas tres líneas se crea un nuevo contenedor llamado docker.translate que se expone en el puerto 56733. Finalmente, vincula el directorio actual al directorio ```/var/www``` del contenedor.

El indicador ```-d``` se utiliza para iniciar un contenedor en el modo de demonio, o como proceso en segundo plano. El indicador ```-p``` se incluye para vincular un puerto del servidor a un puerto concreto del contenedor Docker. En este caso, vinculará el puerto ```56733``` al puerto ```80``` en el contenedor Docker. El indicador ```-v``` especifica un volumen de Docker para montarlo en el contenedor y, en este caso, se montará todo el directorio del proyecto en la carpeta ```/var/www``` del contenedor de Docker.

Para probar la creación de la imagen de Docker y un contenedor a partir de la imagen resultante, ejecute:

```shell
sudo bash start.sh
```

Una vez que la secuencia de comandos termine de ejecutarse, utilice el siguiente comando para enumerar todos los contenedores en ejecución:

```shell
sudo docker ps
```

Verá el contenedor docker.translate en ejecución. Ahora que se está ejecutando, visite la dirección IP en el puerto especificado de su navegador: http://```dominio```.

XXXXXXXXX


## Paso 3: Presentar archivos de plantillas

Las [plantillas](https://flask.palletsprojects.com/en/1.0.x/tutorial/templates/) son archivos que muestran contenido estático y dinámico a los usuarios que visitan su aplicación. En este paso, creará una plantilla HTML con el propósito de producir una página de inicio para la aplicación.

El archivo ```index.html``` pertenece al directorio ```app/templates```:

```html
<!doctype html>

<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>Traductor Inglés - Español</title>
  </head>
  <body>
    <h2>Traductor Inglés - Español</h2>
    <div>
      <form action="/result" method="POST">
        <label for="English">Frase a traducir: </label>
        <input type="text" id="English" name="English">
        <br>
        <br>
        <input type="submit" value="Traducir">
      </form>
    </div>
  </body>
</html>
```

Por otra parte, se ha creado otro template para el resultado de la traducción ```result.html```:

```html
<!doctype html>

<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>Traductor Inglés - Español</title>
  </head>
   <body>
      <h2>Traductor Inglés - Español</h2>
   <div>
      <form action="/index" method="GET">
         <h4>Frase a traducir del inglés: </h4>
         <label>    {{ sentence }} </label>
         <h4>Frase traducida al español: </h4>
         <label>    {{ prediction }} </label>
         <br>
         <br>
         <input type="submit" value="Volver">
         <br>
      </form>
   </body>
</html>
```

## Paso 4: Desplegar Aplicación

Para que estos cambios se apliquen, deberá detener y reiniciar los contenedores de Docker. Ejecute el siguiente comando para volver a compilar el contenedor:

```shell
sudo docker stop docker.translate && sudo docker start docker.translate
```

Visite su aplicación en http://```your-domain```:56733 desde un navegador externo al servidorpara ver la la aplicación.


## Paso 5: Actualizar la aplicación

A veces, deberá realizar en la aplicación cambios que pueden incluir instalar nuevos requisitos, actualizar el contenedor de Docker o aplicar modificaciones vinculadas al HTML y a la lógica. A lo largo de esta sección, configurará touch-reload para realizar estos cambios sin necesidad de reiniciar el contenedor de Docker.

```Autoreloading``` de Python controla el sistema completo de archivos en busca de cambios y actualiza la aplicación cuando detecta uno. No se aconseja el uso de _autoreloading_ en producción porque puede llegar a utilizar muchos recursos de forma muy rápida. En este paso, utilizará touch-reload para realizar la verificación en busca de cambios en un archivo concreto y volver a cargarlo cuando se actualice o sustituya.

Para implementar esto, abra el archivo uwsgi.ini:

```python
module = main
callable = app
master = true
touch-reload = /app/uwsgi.ini
```

Esto especifica un archivo que se modificará para activar una recarga completa de la aplicación.

A continuación, si hace una modificación en cualquier _template_ y abre la página de inicio de su aplicación en http://```your-domain```:56733 observará que los cambios no se reflejan. Esto se debe a que la condición para volver a cargar es un cambio en el archivo uwsgi.ini. Para volver a cargar la aplicación, use touch a fin de activar la condición:

```shell
sudo touch uwsgi.ini
```


## Conclusiones
A través de este tutorial, se ha una aplicación de Flask y su implementación en un contenedor de Docker. También se configuró touch-reload para actualizar su aplicación sin necesidad de reiniciar el contenedor.

Con su nueva aplicación en Docker, ahora podrá realizar el escalamiento de forma sencilla. Para obtener más información sobre el uso de Docker, consulte su [documentación oficial.](https://docs.docker.com/)
