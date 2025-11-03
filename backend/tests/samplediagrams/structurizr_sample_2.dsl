workspace {
  model {
    admin = person "Admin"
    crm = softwareSystem "CRM System" {
      ui = container "UI"
      api = container "API"
      db = container "Database"
      admin -> ui "Uses"
      ui -> api "Calls"
      api -> db "Reads/Writes"
    }
  }
  views {
    container crm {
      include *
      autolayout lr
    }
  }
}