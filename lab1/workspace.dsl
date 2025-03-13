workspace {
    name "Service Ordering Platform"
    !identifiers hierarchical

    model {
        user = Person "User"
        admin = Person "Admin"

        servicePlatform = softwareSystem "Service Ordering Platform" {
            users_service = container "User Service" {
                technology "Python FastAPI"
                tags "auth"
                component "Authentication Management"
                component "User Profile Management"
            }

            service_service = container "Service Service" {
                technology "Python FastAPI"
                tags "service"
                component "Service Listing"
                component "Service Search"
                component "Service Management"
            }

            order_service = container "Order Service" {
                technology "Python FastAPI"
                tags "order"
                component "Order Placement"
                component "Order Tracking"
                component "Payment Processing"
            }
        }

        user -> servicePlatform.users_service "Регистрация и аутентификация" "REST"
        user -> servicePlatform.service_service "Просмотр услуг" "REST"
        user -> servicePlatform.order_service "Управление заказами" "REST"
        admin -> servicePlatform.service_service "Управление услугами" "REST"
        admin -> servicePlatform.order_service "Отслеживание заказов" "REST"
        
        servicePlatform.order_service -> servicePlatform.order_service "Обработка платежа" "REST"
        servicePlatform.order_service -> servicePlatform.order_service "Обновление статуса заказа" "REST"
        
        servicePlatform.service_service -> servicePlatform.service_service "Обновление информации об услуге" "REST"
        servicePlatform.service_service -> servicePlatform.service_service "Удаление услуги" "REST"
        servicePlatform.service_service -> user "Услуга отображается в каталоге" "REST"

        // Добавлена связь между Service Service и Order Service
        servicePlatform.service_service -> servicePlatform.order_service "Инициация оформления заказа" "REST"

        deploymentEnvironment "PROD" {
            deploymentNode "Cloud" {
                deploymentNode "Kubernetes Cluster" {
                    api_gateway = infrastructureNode "API Gateway"
                    db = infrastructureNode "PostgreSQL Database"
                    
                    users_pod = deploymentNode "users-pod" {
                        instances 3
                        containerInstance servicePlatform.users_service
                    }
                    services_pod = deploymentNode "services-pod" {
                        instances 3
                        containerInstance servicePlatform.service_service
                    }
                    orders_pod = deploymentNode "orders-pod" {
                        instances 3
                        containerInstance servicePlatform.order_service
                    }
                    
                    api_gateway -> users_pod "Маршрутизация пользовательских запросов"
                    api_gateway -> services_pod "Маршрутизация запросов к услугам"
                    api_gateway -> orders_pod "Маршрутизация запросов к заказам"
                    users_pod -> db "Хранение данных пользователей"
                    services_pod -> db "Хранение данных об услугах"
                    orders_pod -> db "Хранение данных заказов"
                }
            }
        }
    }

    views {
        themes default

        systemContext servicePlatform "context" {
            include *
            exclude relationship.tag==video
            autoLayout
        }

        container servicePlatform "containers" {
            include *
            autoLayout
        }

        component servicePlatform.users_service "users_components" {
            include *
            autoLayout
        }

        component servicePlatform.service_service "service_components" {
            include *
            autoLayout
        }

        component servicePlatform.order_service "order_components" {
            include *
            autoLayout
        }

        deployment * "PROD" {
            include *
            autoLayout
        }

        dynamic servicePlatform "order_flow" "Обработка заказа от добавления услуги до завершения" {
            autoLayout lr
            user -> servicePlatform.service_service "Добавление услуг в заказ"
            servicePlatform.service_service -> servicePlatform.order_service "Инициация оформления заказа"
            servicePlatform.order_service -> servicePlatform.order_service "Обработка платежа"
            servicePlatform.order_service -> servicePlatform.order_service "Обновление статуса заказа"
            servicePlatform.order_service -> user "Подтверждение оформления заказа"
        }
        
        dynamic servicePlatform "service_management" "Управление услугами администратором" {
            autoLayout lr
            admin -> servicePlatform.service_service "Добавление новой услуги"
            servicePlatform.service_service -> servicePlatform.service_service "Обновление информации об услуге"
            servicePlatform.service_service -> user "Услуга отображается в каталоге"
        }
    }
}
