# Base de datos y motores soportados

## Motor por defecto

- SQLite (`sqlite:///./app.db`)

## Motores soportados

- MySQL
- MariaDB
- SQL Server

## Configuracion

Se define con `DATABASE_URL` en `.env`.

### SQLite

```env
DATABASE_URL=sqlite:///./app.db
```

### MySQL

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/mydb
```

### MariaDB

```env
DATABASE_URL=mariadb+mariadbconnector://root:password@localhost:3306/mydb
```

### SQL Server

```env
DATABASE_URL=mssql+pyodbc://sa:YourStrong!Passw0rd@localhost:1433/mydb?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

## Nota de portabilidad

El proyecto detecta SQLite para usar modo batch en migraciones.
Esto ayuda con operaciones DDL limitadas en SQLite.
