workspace {
    name "FaceBook"
    description "Социальная сеть"
    
    model {
        user = person "Пользователь" {
            description "Активный пользователь социальной сети"
        }
    
        socialNetwork = softwareSystem "Социальная сеть" {
            description "Распределенная платформа социального взаимодействия на основе микросервисов"
    
            # User Context Microservices
            userService = container "User Service" {
                description "Сервис управления пользователями и профилями"
                technology "Python"
            }
    
            userDatabase = container "User Database" {
                description "База данных пользовательских профилей"
                technology "PostgreSQL"
            }
    
            # Messaging Context Microservices
            messagingService = container "Messaging Service" {
                description "Сервис обмена сообщениями и чатов"
                technology "Python"
            }
    
            messagingDatabase = container "Messaging Database" {
                description "База данных сообщений и чатов"
                technology "MongoDB"
            }
    
            # Social Interaction Context Microservices
            socialInteractionService = container "Social Interaction Service" {
                description "Сервис социальных взаимодействий"
                technology "Python"
            }
    
            socialInteractionDatabase = container "Social Interaction Database" {
                description "База данных постов и социальных связей"
                technology "PostgreSQL"
            }
    
            # API Gateway
            apiGateway = container "API Gateway" {
                description "Единая точка входа для всех клиентских запросов"
                technology "Python/FastAPI/Nginx"
            }
    
            # Frontend
            frontend = container "Web Frontend" {
                description "Клиентское веб-приложение"
                technology "React.js"
            }
    
            # Relationships
            user -> frontend "Взаимодействует"
            frontend -> apiGateway "Отправляет запросы"
            
            apiGateway -> userService "Маршрутизация запросов пользователей"
            apiGateway -> messagingService "Маршрутизация запросов сообщений"
            apiGateway -> socialInteractionService "Маршрутизация социальных взаимодействий"
    
            userService -> userDatabase "Управление данными"
            messagingService -> messagingDatabase "Управление сообщениями"
            socialInteractionService -> socialInteractionDatabase "Управление взаимодействиями"
        }
    }

views {
    systemContext socialNetwork {
        include *
        autoLayout lr
    }

    container socialNetwork {
        include *
        autoLayout lr
    }

    dynamic socialNetwork {
        user -> frontend "Регистрация"
        frontend -> apiGateway "POST /register"
        apiGateway -> userService "Создание профиля"
        userService -> userDatabase "Сохранение данных"
        autoLayout lr
    }

    dynamic socialNetwork {
        user -> frontend "Отправка сообщения"
        frontend -> apiGateway "POST /message"
        apiGateway -> messagingService "Маршрутизация сообщения"
        messagingService -> messagingDatabase "Сохранение сообщения"
        autoLayout lr
    }
}
}
