package teamtwo.pay.apps.teamrubicon;

import android.Manifest;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.location.LocationManager;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.AsyncTask;
import android.os.Build;
import android.support.design.widget.Snackbar;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import teamtwo.pay.apps.teamrubicon.connectors.Config;
import teamtwo.pay.apps.teamrubicon.connectors.JSONParser;

public class MainActivity extends AppCompatActivity {

    EditText enterEmail, enterBand;

    Button btnTrack;

    ProgressDialog dialog;

    List<NameValuePair> details;

    String response;

    JSONParser jsonParser = new JSONParser();

    String myemail;
    String mybandno;

    LocationManager locationManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        //Stop GPS service in case it was started before
        Intent intent = new Intent(getApplicationContext(), GPSService.class);
        stopService(intent);

        //Request permissions
        if (ActivityCompat.checkSelfPermission(this, android.Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED ||
                ActivityCompat.checkSelfPermission(this, android.Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            // TODO: Consider calling
            //    ActivityCompat#requestPermissions
            // here to request the missing permissions, and then overriding
            //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
            //                                          int[] grantResults)
            // to handle the case where the user grants the permission. See the documentation
            // for ActivityCompat#requestPermissions for more details.
            List<String> permissions = new ArrayList<String>();
            permissions.add(android.Manifest.permission.ACCESS_FINE_LOCATION);
            permissions.add(android.Manifest.permission.ACCESS_COARSE_LOCATION);

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                requestPermissions( permissions.toArray( new String[permissions.size()] ), 101 );
            }
            //return;
        }

        //Request user to enable location
        ConnectivityManager cm = (ConnectivityManager)getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo netInfo = cm.getActiveNetworkInfo();
        if (netInfo != null && netInfo.isConnected()) {
            locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
            if(!locationManager.isProviderEnabled( LocationManager.GPS_PROVIDER )){
                buildAlertMessageNoGps();
            }
        }
        else{
            for(int i=0; i < 2; i++){
                Toast.makeText(getBaseContext(), "Please check/enable your internet connection then try again", Toast.LENGTH_LONG).show();
            }
        }

        enterEmail = (EditText) findViewById(R.id.enterEmail);
        enterBand = (EditText) findViewById(R.id.enterBandNo);

        btnTrack = (Button) findViewById(R.id.btnTrack);
        btnTrack.setOnClickListener(new View.OnClickListener(){

            @Override
            public void onClick(View v) {
                if(enterEmail.getText().toString().length()>0 && enterBand.getText().toString().length()>0){
                    new checkLogin(enterEmail.getText().toString(), enterBand.getText().toString()).execute();
                }
                else {
                    Toast.makeText(getBaseContext(), "Please fill in all fields", Toast.LENGTH_LONG).show();
                }
            }
        });
    }

    private void buildAlertMessageNoGps() {
        final AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setMessage("Your GPS is disabled. Please enable it in order to allow us to keep track of you for your safety.")
                .setCancelable(false)
                .setPositiveButton("Enable GPS", new DialogInterface.OnClickListener() {
                    public void onClick(@SuppressWarnings("unused") final DialogInterface dialog, @SuppressWarnings("unused") final int id) {
                        startActivity(new Intent(android.provider.Settings.ACTION_LOCATION_SOURCE_SETTINGS));
                    }
                })
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    public void onClick(final DialogInterface dialog, @SuppressWarnings("unused") final int id) {
                        dialog.cancel();
                    }
                });
        final AlertDialog alert = builder.create();
        alert.show();
    }

    class checkLogin extends AsyncTask<String, String, String> {

        public checkLogin(String email, String bandno) {

            details = new ArrayList<NameValuePair>();
            details.add(new BasicNameValuePair("email", email));
            details.add(new BasicNameValuePair("bandno", bandno));

            myemail = email;
            mybandno = bandno;
        }

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            //show progress dialog
            dialog = new ProgressDialog(MainActivity.this);
            dialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
            dialog.setMessage("One moment...");
            dialog.show();
        }

        @Override
        protected String doInBackground(String... params) {
            try {
                // getting JSON Object
                JSONObject json = jsonParser.makeHttpRequest(Config.SERVER_URL+"authtracker",
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
                dialog.dismiss();
                getResponse = response;

                //if(getResponse.equals("1")){
                    try{
                        //Initialize GPS tracking
                        Intent gpsintent = new Intent(getApplicationContext(), GPSService.class);
                        startService(gpsintent);

                        //Store phone number in sharedpref session
                        SharedPreferences pref = getSharedPreferences("MyPref", 1); // 0 - for private mode
                        SharedPreferences.Editor editor = pref.edit();
                        editor.putString("email", myemail);
                        editor.commit();

                        System.out.println("Email is saved: "+myemail);

                        //Initialize GPS tracking
                        Intent intent = new Intent(getApplicationContext(), GPSService.class);
                        startService(intent);

                        Intent home = new Intent(getBaseContext(), Track.class);
                        startActivity(home);
                    }
                    catch(Exception r){
                        r.printStackTrace();
                    }
                //}
                //else{
                //    Toast.makeText(getBaseContext(), "Error verifying your details. Please try again.", Toast.LENGTH_LONG).show();
                //git commi}
            }catch(Exception r){
                r.printStackTrace();
            }
        }
    }
}
