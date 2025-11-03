workspace {
  model {
    user = person "User"
    analytics = softwareSystem "Analytics Platform" {
      dashboard = container "Dashboard"
      engine = container "Analytics Engine"
      db = container "Data Warehouse"
      user -> dashboard "Views metrics"
      dashboard -> engine "Requests analysis"
      engine -> db "Reads data"
    }
  }
  views {
    container analytics {
      include *
      autolayout lr
    }
  }
}