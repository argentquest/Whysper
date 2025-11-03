workspace {
      model {
        user = person "User"
        softwareSystem = softwareSystem "E-Commerce System" {
          webapp = container "Web Application"
          database = container "Database"
          user -> webapp "Uses"
          webapp -> database "Reads and writes"
        }
      }
      views {
        systemContext softwareSystem {
          include *
          autolayout lr
        }
      }
    }