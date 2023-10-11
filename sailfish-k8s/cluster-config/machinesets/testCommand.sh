helm template . --set clusterName=pearl-tst-s4pgx,networkResourceGroup=rg-pearl-001,clusterVnet=pearl-tst-vnet,aroResourceGroup=rg-aro-pearl-001,vmSize=Standard_D16as_v5 > output.yaml

oc apply -f output.yaml