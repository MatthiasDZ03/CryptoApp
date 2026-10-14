namespace AccountService.Settings;

public class ApiKeySettings
{
    public string HeaderName { get; set; } = "X-Api-Key";
    public string Key { get; set; } = "";
}