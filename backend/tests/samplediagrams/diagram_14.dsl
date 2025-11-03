workspace {
      model {
        user = person "User 4"
        system = softwareSystem "System 4" {
          frontend = container "Frontend 4"
          backend = container "Backend 4"
          db = container "Database 4"
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