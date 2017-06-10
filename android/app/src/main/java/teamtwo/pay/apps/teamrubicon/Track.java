package teamtwo.pay.apps.teamrubicon;

import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;

import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import teamtwo.pay.apps.teamrubicon.connectors.Config;
import teamtwo.pay.apps.teamrubicon.connectors.JSONParser;

/**
 * Created by kenneth on 6/10/17.
 */

public class Track extends AppCompatActivity {

    Button btnStopTrack, btnEmergency;

    List<NameValuePair> details;

    String response;

    JSONParser jsonParser = new JSONParser();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_tracking);

        btnStopTrack = (Button) findViewById(R.id.btnStopTracking);
        btnStopTrack.setOnClickListener(new View.OnClickListener(){

            @Override
            public void onClick(View v) {
                //Close the users session
                SharedPreferences pref = getSharedPreferences("MyPref", 1); // 0 - for private mode
                SharedPreferences.Editor editor = pref.edit();
                editor.remove("email");
                editor.commit();

                //Stop GPS service
                //Initialize GPS tracking
                Intent intent = new Intent(getApplicationContext(), GPSService.class);
                stopService(intent);

                Intent main = new Intent(getBaseContext(), MainActivity.class);
                startActivity(main);
                finish();
            }
        });

        btnEmergency = (Button) findViewById(R.id.btnEmergency);
        btnEmergency.setOnClickListener(new View.OnClickListener(){

            @Override
            public void onClick(View v) {
                new requestHelp().execute();
            }
        });
    }

    class requestHelp extends AsyncTask<String, String, String> {

        public requestHelp() {

            //Get last known coordinates from GPS service
            GPSService myLoc = new GPSService();

            details = new ArrayList<NameValuePair>();
            details.add(new BasicNameValuePair("lat", myLoc.myLat));
            details.add(new BasicNameValuePair("lon", myLoc.myLon));

            System.out.println("HELP LAT: "+myLoc.myLat);
            System.out.println("HELP LON: "+myLoc.myLon);
        }

        @Override
        protected String doInBackground(String... params) {
            try {
                //Get email of use from shared preferences
                SharedPreferences pref = getSharedPreferences("MyPref", 1); // 0 - for private mode
                String email = pref.getString("email", "email");
                details.add(new BasicNameValuePair("email", email));

                System.out.println("EMAIL: "+email);

                // getting JSON Object
                JSONObject json = jsonParser.makeHttpRequest(Config.SERVER_URL+"danger",
                        "POST", details);

                // check log cat fro response
                Log.d("Create Response", json.toString());

                // check for success tag
                //success = json.getString("status");
                response = json.getString("status");
                System.out.println(response);

            } catch (Exception e) {
                e.printStackTrace();
                response = "Connection error. Please try again";
            }
            return response;
        }

        protected void onPostExecute(String getResponse) {
            // dismiss the dialog once done
            try{

                getResponse = response;
                Log.d("Response", getResponse);

                if(getResponse.equals("1")){
                    successDialog();
                }
                else{
                    Toast.makeText(getBaseContext(), "Sorry an error occured, please try again", Toast.LENGTH_LONG).show();
                }

            }catch(Exception r){
                r.printStackTrace();
            }
        }
    }

    private void successDialog() {
        final AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setMessage("You have successfully notified TeamRubicon. Help is on the way")
                .setCancelable(false)
                .setPositiveButton("OK", new DialogInterface.OnClickListener() {
                    public void onClick(@SuppressWarnings("unused") final DialogInterface dialog, @SuppressWarnings("unused") final int id) {

                    }
                });
        final AlertDialog alert = builder.create();
        alert.show();
    }
}
