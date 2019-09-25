# Get the current master branch of BART and pull it
git fetch bart master
git subtree pull --prefix bart bart master --squash
