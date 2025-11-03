workspace {
      model {
        user = person "User 1"
        system = softwareSystem "System 1" {
          frontend = container "Frontend 1"
          backend = container "Backend 1"
          db = container "Database 1"
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