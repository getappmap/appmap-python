import java.util.HashMap;
import java.util.Map;

public class AppMap {

    private Map<String, Object> data;

    /**
     * 
     */
    public AppMap() {
        this.data = new HashMap<>();
    }

    /**
     * @param key
     * @param value
     */
    public void addData(String key, Object value) {
        this.data.put(key, value);
    }

    public Object getData(String key) {
        return this.data.get(key);
    }

    public void removeData(String key) {
        this.data.remove(key);
    }

    public boolean hasData(String key) {
        return this.data.containsKey(key);
    }

    public int size() {
        return this.data.size();
    }

    @Override
    public String toString() {
        return this.data.toString();
    }

}
