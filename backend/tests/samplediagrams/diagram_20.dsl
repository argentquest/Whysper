workspace {
      model {
        user = person "User 10"
        system = softwareSystem "System 10" {
          frontend = container "Frontend 10"
          backend = container "Backend 10"
          db = container "Database 10"
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