workspace {
      model {
        user = person "User 6"
        system = softwareSystem "System 6" {
          frontend = container "Frontend 6"
          backend = container "Backend 6"
          db = container "Database 6"
          user -> frontend "Uses"
          frontend -> backend "Calls"
          backend -> db "Stores data"
        }
      }
      views {
        container system {
          include *
          autolayout lr
        }
      }
    }