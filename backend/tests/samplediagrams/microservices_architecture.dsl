
workspace {

    model {
        user = person "User"
        softwareSystem = softwareSystem "E-Commerce System" {
            webApp = container "Web Application" {
                user -> this "Uses"
            }
            api = container "API Gateway"
            user -> api "Interacts with"
            webApp -> api "Sends requests"
            orderService = container "Order Service"
            paymentService = container "Payment Service"
            api -> orderService "Routes to"
            api -> paymentService "Routes to"
        }
    }

    views {
        systemContext softwareSystem {
            include *
            autolayout lr
        }
        container softwareSystem {
            include *
            autolayout lr
        }
        theme default
    }
}
