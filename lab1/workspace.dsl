workspace {
    name "Social Network Platform"
    !identifiers hierarchical

    model {
        user = Person "User"
        admin = Person "Admin"

        socialNetwork = softwareSystem "Social Network Platform" {
            users_service = container "User Service" {
                technology "Python FastAPI"
                tags "auth"
                component "Authentication Management"
                component "User Profile Management"
            }

            wall_service = container "Wall Service" {
                technology "Python FastAPI"
                tags "wall"
                component "Post Management"
                component "Wall Feed"
            }

            chat_service = container "Chat Service" {
                technology "Python FastAPI"
                tags "chat"
                component "Message Management"
                component "Chat History"
            }
        }

        user -> socialNetwork.users_service "Регистрация и аутентификация" "REST"
        user -> socialNetwork.wall_service "Добавление записи на стену" "REST"
        user -> socialNetwork.chat_service "Отправка сообщения" "REST"
        admin -> socialNetwork.users_service "Управление пользователями" "REST"
        
        socialNetwork.wall_service -> socialNetwork.wall_service "Обновление ленты стены" "REST"
        socialNetwork.chat_service -> socialNetwork.chat_service "Обновление истории чата" "REST"
        
        deploymentEnvironment "PROD" {
            deploymentNode "Cloud" {
                deploymentNode "Kubernetes Cluster" {
                    api_gateway = infrastructureNode "API Gateway"
                    db = infrastructureNode "PostgreSQL Database"
                    
                    users_pod = deploymentNode "users-pod" {
                        instances 3
                        containerInstance socialNetwork.users_service
                    }
                    wall_pod = deploymentNode "wall-pod" {
                        instances 3
                        containerInstance socialNetwork.wall_service
                    }
                    chat_pod = deploymentNode "chat-pod" {
                        instances 3
                        containerInstance socialNetwork.chat_service
                    }
                    
                    api_gateway -> users_pod "Маршрутизация пользовательских запросов"
                    api_gateway -> wall_pod "Маршрутизация запросов к стене"
                    api_gateway -> chat_pod "Маршрутизация запросов к чату"
                    users_pod -> db "Хранение данных пользователей"
                    wall_pod -> db "Хранение данных стены"
                    chat_pod -> db "Хранение данных чата"
                }
            }
        }
    }

    views {
        themes default

        systemContext socialNetwork "context" {
            include *
            exclude relationship.tag==video
            autoLayout
        }

        container socialNetwork "containers" {
            include *
            autoLayout
        }

        component socialNetwork.users_service "users_components" {
            include *
            autoLayout
        }

        component socialNetwork.wall_service "wall_components" {
            include *
            autoLayout
        }

        component socialNetwork.chat_service "chat_components" {
            include *
            autoLayout
        }

        deployment * "PROD" {
            include *
            autoLayout
        }

        dynamic socialNetwork "post_to_wall" "Процесс добавления записи на стену" {
            autoLayout lr
            user -> socialNetwork.wall_service "Добавление записи на стену"
            socialNetwork.wall_service -> socialNetwork.wall_service "Обновление ленты стены"
            socialNetwork.wall_service -> user "Подтверждение добавления записи"
        }
        
        dynamic socialNetwork "send_message" "Процесс отправки сообщения" {
            autoLayout lr
            user -> socialNetwork.chat_service "Отправка сообщения"
            socialNetwork.chat_service -> socialNetwork.chat_service "Обновление истории чата"
            socialNetwork.chat_service -> user "Подтверждение отправки сообщения"
        }
    }
}
