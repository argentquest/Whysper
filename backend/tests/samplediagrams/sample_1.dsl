workspace {
  model {
    user = person "User"
    softwareSystem = softwareSystem "System A" {
      webapp = container "Web App"
      db = container "Database"
      user -> webapp "Uses"
      webapp -> db "Reads/Writes"
    }
  }
  views {
    systemContext softwareSystem {
      include *
      autolayout lr
    }
  }
}