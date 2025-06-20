# Получить дату и время для имени файла
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupFile = "backup_$timestamp.sql"
$backupPath = ".\backups\$backupFile"

# Имя контейнера
$container = "pg_database"

# Имя БД, пользователь
$envVars = @{}
Get-Content .env | ForEach-Object {
    if ($_ -match "^(.*?)=(.*)$") {
        $envVars[$matches[1]] = $matches[2]
    }
}

$db = $envVars["DB_NAME"]
$user = $envVars["DB_USER"]

# Если не удалось автоматически считать, можешь прописать вручную:
# $db = "images_db"
# $user = "postgres"

# Основная команда
Write-Host "Выполняется резервное копирование базы $db..."
docker exec -t $container pg_dump -U $user $db > $backupPath

if (Test-Path $backupPath) {
    Write-Host "Бэкап успешно сохранён: $backupPath"
} else {
    Write-Host "Ошибка: файл не создан!"
}