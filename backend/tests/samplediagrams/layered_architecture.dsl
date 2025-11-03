
workspace {

    model {
        user = person "User"
        softwareSystem = softwareSystem "Inventory Management System" {
            ui = container "User Interface"
            businessLogic = container "Business Logic Layer"
            dataAccess = container "Data Access Layer"
            database = container "Database"

            user -> ui "Uses"
            ui -> businessLogic "Invokes"
            businessLogic -> dataAccess "Calls"
            dataAccess -> database "Queries"
        }
    }

    views {
        container softwareSystem {
            include *
            autolayout lr
        }
        theme default
    }
}
