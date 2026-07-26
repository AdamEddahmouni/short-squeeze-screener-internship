package Screener;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;



public class ScreenerModel{
    private String tickerSymbol = "";
    /*private boolean checkboxStates1;
    private boolean checkboxStates2;
    private boolean checkboxStates3;
    private boolean checkboxStates4;
    private boolean checkboxStates5;
    private String selectedLikelihood = "";*/
    private Map<String, String> stockData = new HashMap<>();
    
    

    public String getTickerSymbol(){
         return tickerSymbol;
    }

    public void setTickerSymbol(String tickerSymbol){
        this.tickerSymbol = tickerSymbol;
    }


    /*public void setCheckboxState(int index, boolean value) {
        switch (index) {
            case 1: checkboxStates1 = value; break;
            case 2: checkboxStates2 = value; break;
            case 3: checkboxStates3 = value; break;
            case 4: checkboxStates4 = value; break;
            case 5: checkboxStates5 = value; break;
            default: throw new IllegalArgumentException("Checkbox index must be 1-5");
        }
    }

    public int getBoxStates(){
        int count = 0;
        if (checkboxStates1) {
            count++;
        }
        if (checkboxStates2) {
            count++;
        }
        if (checkboxStates3) {
            count++;
        }
        if (checkboxStates4) {
            count++;
        }
        if (checkboxStates5) {
            count++;
        }

        return count;
    }
    
    public void setLikelihood(){
        if (getBoxStates() == 5) {
            selectedLikelihood = "High Likelyhood";
        }else if (getBoxStates() == 4) {
            selectedLikelihood = "Medium Likelyhood";
        
        }else{
            selectedLikelihood = "Low Likelyhood";
        }
    }

    public String getSelectedLikelihood(){
        return selectedLikelihood;
    }*/

    //Doesn't Work
    /*public void setJLables(){
        try{
            price.setText("Share Price: $" + stockData.get("Price"));
            change.setText("Percent Change: " + stockData.get("Change"));
            relVol.setText("Relative Volume: "   + stockData.get("Rel Vol"));
            floatAmt.setText("Float Amount: " + stockData.get("Float"));
        }
        catch (IOException exception){
            System.err.println("Failed to fetch data for " + tickerSymbol);
        }

    }*/


    public Map<String, String> getStockData() {
        return stockData;
    }

    public void fetchFinvizData() {
        try {
            this.stockData = FinvizScraper.getStockData(tickerSymbol);
            System.out.println("Data for " + tickerSymbol + ": " + stockData);
        } catch (IOException e) {
            System.err.println("Failed to fetch data for " + tickerSymbol);
            stockData.clear();
        }
    }
    public void setJlabels(){
        
    }
}


