
workspace {
    model {
        user = person "User"
        system = softwareSystem "System 16" {
            frontend = container "Frontend"
            backend = container "Backend"
            database = container "Database"

            user -> frontend "Uses"
            frontend -> backend "Sends requests"
            backend -> database "Reads/Writes"
        }
    }

    views {
        container system {
            include *
            autolayout lr
        }
        theme default
    }
}
