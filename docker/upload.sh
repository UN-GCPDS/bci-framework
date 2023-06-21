#!/bin/bash

# Verificar si se proporcionó el nombre del archivo Dockerfile como argumento
if [ $# -ne 1 ]; then
  echo "Uso: $0 <nombre-del-archivo-dockerfile>"
  exit 1
fi

DOCKERFILE="$1"

# Buscar las líneas LABEL en el archivo Dockerfile
LABEL_LINES=$(grep "^LABEL" "$DOCKERFILE")

# Extraer el valor de la etiqueta "image"
IMAGE_NAME=$(echo "$LABEL_LINES" | grep "image" | awk -F'="' '{print $2}' | awk -F'"' '{print $1}')

# Extraer el valor de la etiqueta "version"
VERSION=$(echo "$LABEL_LINES" | grep "version" | awk -F'="' '{print $2}' | awk -F'"' '{print $1}')

# Verificar si se encontraron las etiquetas
if [[ -z "$IMAGE_NAME" || -z "$VERSION" ]]; then
  echo "No se encontraron las etiquetas 'image' y 'version' en el Dockerfile."
  exit 1
fi

# Construir la imagen
docker build -t "$IMAGE_NAME":"$VERSION" -f "$DOCKERFILE" .

# Etiquetar la imagen con "latest"
docker tag "$IMAGE_NAME":"$VERSION" "$IMAGE_NAME":latest

# Iniciar sesión en Docker Hub
docker login

# Subir la imagen etiquetada a Docker Hub
docker push "$IMAGE_NAME":"$VERSION"
docker push "$IMAGE_NAME":latest
