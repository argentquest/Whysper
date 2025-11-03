workspace {
  model {
    user = person "User"
    analytics = softwareSystem "Analytics Platform" {
      container dashboard "Dashboard"
      container engine "Analytics Engine"
      container db "Data Warehouse"
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