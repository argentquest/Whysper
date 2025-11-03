workspace {
  model {
    user = person "User"
    system = softwareSystem "System" {
      web = container "Web App"
      db = container "Database"
      user -> web "Uses"
      web -> db "Reads/Writes"
    }
  }
  views {
    systemContext system {
      include *
      autolayout lr
    }
  }
}