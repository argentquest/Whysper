workspace {
      model {
        user = person "User 2"
        system = softwareSystem "System 2" {
          frontend = container "Frontend 2"
          backend = container "Backend 2"
          db = container "Database 2"
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