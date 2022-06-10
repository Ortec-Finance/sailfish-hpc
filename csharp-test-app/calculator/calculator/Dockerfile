FROM mcr.microsoft.com/dotnet/aspnet:6.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /src
COPY ["calculator/calculator.csproj", "calculator/"]
RUN dotnet restore "calculator/calculator.csproj"
COPY . .
WORKDIR "/src/calculator"
RUN dotnet build "calculator.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "calculator.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "calculator.dll"]
