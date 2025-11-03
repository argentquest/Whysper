workspace {
  model {
    user = person "User"
    softwareSystem = softwareSystem "System A" {
      container webapp "Web App"
      container db "Database"
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