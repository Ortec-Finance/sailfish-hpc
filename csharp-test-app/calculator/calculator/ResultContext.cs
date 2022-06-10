using System;
using Microsoft.EntityFrameworkCore;

namespace calculator
{
    class ResultContext: DbContext
    {
        public ResultContext(ILogger logger)
        {
            _logger = logger;
        }

        private ILogger _logger;
        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            var connection = Environment.GetEnvironmentVariable("DB_CONNECTION") ?? "Server=localhost;Port=5432;Database=myDatabase;User Id=myUsername;Password=myPassword;";
            _logger.Log(LogLevel.Information, "connection string: {0}", connection);
            Console.WriteLine(connection);
            optionsBuilder.UseNpgsql(connection);
        // optionsBuilder.UseSqlServer(builder.ConnectionString);
        }
            
        
        public DbSet<Result> Results => Set<Result>();
        
        protected override void OnModelCreating(ModelBuilder mb)
        {
            base.OnModelCreating(mb);

            mb.Entity<Result>().HasKey(rc => new {rc.ResultsGroup, rc.TaskId});
        }
    }
}