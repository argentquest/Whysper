workspace {
      model {
        admin = person "Administrator"
        cms = softwareSystem "Content Management System" {
          frontend = container "Frontend"
          backend = container "Backend"
          db = container "Database"
          admin -> frontend "Manages content"
          frontend -> backend "Sends requests"
          backend -> db "Stores content"
        }
      }
      views {
        container cms {
          include *
          autolayout lr
        }
      }
    }