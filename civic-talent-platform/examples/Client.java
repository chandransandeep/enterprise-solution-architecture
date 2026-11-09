import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class Client {
    public static void main(String[] args) throws Exception {
        String key = System.getenv().getOrDefault("DEMO_API_KEY", "local-development-only");
        var request = HttpRequest.newBuilder(URI.create("http://localhost:8000/v1/vacancies"))
                .header("X-API-Key", key).GET().build();
        var response = HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
        System.out.println(response.statusCode() + " " + response.body());
    }
}
