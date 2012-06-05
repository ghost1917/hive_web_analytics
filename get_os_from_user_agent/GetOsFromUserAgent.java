import org.apache.hadoop.hive.ql.exec.UDF;
import org.apache.hadoop.io.Text;

public class GetOsFromUserAgent extends UDF {
    public Text evaluate(Text str) {
        if (str == null) {
            return null;
        }

        String userAgent = str.toString ();

        if  (userAgent.indexOf ("Windows NT 5.1") != -1) {
            return new Text ("Windows XP");
        }
        else if (userAgent.indexOf ("Mac OS X") != -1) {
            return new Text ("Max OS X");
        }
        else if (userAgent.indexOf ("Windows NT 6.1") != -1) {
            return new Text ("Windows 7");
        }
        else {
            return null;
        }
    }
} 
