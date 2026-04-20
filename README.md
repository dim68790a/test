https://docs.google.com/document/d/1OxlWEItvGYA3h5Xw2SVTNDlPV1f830fRT1CJ_a6mtxI/edit?tab=t.0
sudo su - jenkins

# Создаём новый ключ в правильном формате
ssh-keygen -m PEM -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Смотрим публичный ключ (его нужно добавить на GitHub)
echo "=== Публичный ключ (добавьте на GitHub) ==="
cat ~/.ssh/id_rsa.pub

# Смотрим приватный ключ (его нужно вставить в Jenkins)
echo "=== Приватный ключ (вставьте в Jenkins) ==="
cat ~/.ssh/id_rsa
