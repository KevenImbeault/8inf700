# 8INF700 - Projet final 

## Architecture
Tous roule dans un node Minikube, chaque service utilise des "Horizontal Pod Autoscaler". Le service PostgreSQL utilise un volume persistent pour ses données.   

Le schéma suivant donne une idée de l'arrangement, les pods plus pâle sont les répliques possible via le HPA.
![Architecture](./projetfinal.png)

## Fichiers de configurations

## Commandes utilisés
1. minikube start - Pour lancer minikube
2. kubectl apply -f ./[service] - Utilise les fichiers dans un dossier pour créer les fonctions nécessaire aux services
3. kubectl get hpa -w - Permet de monitor les HPA pour valider leur fonctionnement lors de test de charge.
