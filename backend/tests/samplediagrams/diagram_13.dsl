workspace {
      model {
        user = person "User 3"
        system = softwareSystem "System 3" {
          frontend = container "Frontend 3"
          backend = container "Backend 3"
          db = container "Database 3"
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