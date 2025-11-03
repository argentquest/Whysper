workspace {
      model {
        user = person "User 8"
        system = softwareSystem "System 8" {
          frontend = container "Frontend 8"
          backend = container "Backend 8"
          db = container "Database 8"
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