workspace {
    name "FaceBook"
    description "Социальная сеть"
    
    model {
        user = person "Пользователь/Его стена" {
        }
        socialNetwork = softwareSystem "Социальная сеть" {
            description "Платформа для социального взаимодействия пользователей"

            frontend = container "Web Site" {
                description "Визуальный интерфейс"
                technology "HTML, CSS, JS"
            }
            backend = container "API GateWay" {
                description "API, балансировщик нагрузки"
                technology "Python"
            }

            db = container "DataBase" {
                description "База данных общая"
                technology "PostgreSQL"
            }

            db_cache = container "Cache" {
                description "База данных для регулярных запросов"
                technology "Redis"
            }
        }


        user -> frontend "Использует"
        frontend -> backend "Исполнение запросов"
        backend -> db "Читает и записывает данные/Медленно"
        backend -> db_cache "Читает и записывает данные/Быстро"
        db_cache -> db "Запрашивает недостающие данные"
    }

    views {

        dynamic socialNetwork "uc01" "Запросы к DB"{
            autoLayout lr
            frontend -> backend "Создание нового пользователя"
            backend -> db "POST/new_user/ {login:<>,password:<>}"

            frontend -> backend "Поиск пользователя по логину"
            backend -> db "GET/get_user/login=<>"

            frontend -> backend "Поиск пользователя по маске имя и фамилии"
            backend -> db "GET/get_user_by_name/name=<>,sername=<>"

            frontend -> backend "Добавление записи на стену"
            backend -> db "POST/create_post/ {login:<>, password:<>, content:<>}"

            frontend -> backend "Загрузка стены пользователя"            
            backend -> db "GET/get_user_wall/login=<>"

            frontend -> backend "Отправка сообщения пользователю"
            backend -> db "POST/send_a_message/{login=<>,password=<>,target=<>,body=<>}"

            frontend -> backend "Получение списка сообщения для пользователя"        
            backend -> db "GET/get_chat/login=<>,target=<>"

        }

        themes default 
        systemContext socialNetwork "ContextDiagram" {
            include *
            autoLayout lr
        }
        container socialNetwork {
            include *
            autoLayout lr
        }
    }
}
