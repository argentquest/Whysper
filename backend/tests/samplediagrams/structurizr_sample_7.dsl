workspace {
  model {
    analyst = person "Analyst"
    bi = softwareSystem "BI Tool" {
      dashboard = container "Dashboard"
      datawarehouse = container "Data Warehouse"
      analyst -> dashboard "Views reports"
      dashboard -> datawarehouse "Fetches data"
    }
  }
  views {
    container bi {
      include *
      autolayout lr
    }
  }
}