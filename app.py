#Import library
import streamlit as st 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 

@st.cache_data
def get_weight(A, str):
    n = A.shape[0]
    e_vals, e_vecs = np.linalg.eig(A)
    lamb = max(e_vals)
    w = e_vecs[:, e_vals.argmax()]
    w = w / np.sum(w)  # Normalization
    # Consistency Checking
    ri = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24,
          7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49, 11: 1.51}
    ci = (lamb - n) / (n - 1)
    cr = ci / ri[n]
    print("Normalized eigen vector:")
    print(w)
    print('CR = %f' % cr)
    if cr >= 0.1:
        print("Failed Consistency check of "+str)
        st.error("Failed Consistency check of "+str)

    return w

def plot_graph(x, y, ylabel, title):
    # Generate random colors
    colors = np.random.rand(len(x), 3)
    
    # Create a horizontal bar chart
    fig, ax = plt.subplots()
    bars = ax.bar(y, x, color=colors)
    ax.set_facecolor('#F0F2F6')
    # Set title and axis labels
    ax.set_title(title)
    ax.set_xlabel(ylabel)
    ax.set_ylabel("Values") 
    # Add specific values to each bar
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), va='bottom')
    return fig

@st.cache_data
def calculate_ahp(A, B, n, m, criterias, alternatives):
    priority_vectors = []  # List to store priority vectors
    
    for i in range(0, n):
        for j in range(i, n):
            if i != j:
                A[j][i] = float(1/A[i][j])
    dfA = pd.DataFrame(A)

    # Calculate priority vector for criteria
    W2 = get_weight(A, "Criteria Table")
    priority_vectors.append(W2)  # Append priority vector to the list
    
    # Add priority vector to dataframe
    dfA['Priority Vector'] = W2
    
    # Display dataframe for criteria
    st.markdown(" #### Tabel dari Kriteria dengan nilai Priority Vector")
    st.table(dfA)
    
    for i in range(0, n):
        for j in range(i, n):
            if i != j:
                for k in range(0, m):
                    for l in range(k, m):
                        if k != l:
                            B[i][k][l] = float(1/B[i][l][k])
    
    st.write("---")
    for i in range(0, n):
        dfB = pd.DataFrame(B[i])
        # Calculate priority vector for alternatives
        W3 = get_weight(B[i], "Alternatives Table for Criterion " + criterias[i])
        priority_vectors.append(W3)  # Append priority vector to the list
        
        # Add priority vector to dataframe
        dfB['Priority Vector'] = W3
        
        # Display dataframe for alternatives
        st.markdown(" #### Tabel dari Alternatives untuk Criterion " + criterias[i] + " dengan Priority Vector")
        st.table(dfB)
    
    # Plot graph for criteria weights
    st.pyplot(plot_graph(W2, criterias, "Criteria", "Weights dari Kriteria"))
    
    # Plot graph for optimal alternative weights
    st.pyplot(plot_graph(W3, alternatives, "Alternatif", "Alternatif Optimal untuk Kriteria yang Diberikan"))
    # Interpretasi untuk plot W3
    max_index = np.argmax(W3)
    max_alternative = alternatives[max_index]
    st.write(f"Berdasarkan perhitungan AHP dan juga visualisasi plot dapat dilihat bahwa calon nasabah yang layak mendapatkan kredit dari koperasi kami adalah: {max_alternative}.")
    st.balloons()

def main():
    st.set_page_config(page_title="AHP Calculator", page_icon=":bar_chart:")
    st.header("Kalkulator AHP untuk Kelayakan Kredit Nasabah")

    #Sidebar
    st.sidebar.title("Kriteria & Alternatif")
    cri_options = ["Tempat tinggal", "Pekerjaan", "Penghasilan", "Tanggungan", "Status", "Jumlah Keluarga", "Jumlah Pinjaman"]  # List opsi kriteria
    criterias = st.sidebar.multiselect("Pilih Kriteria", cri_options)  # Memilih beberapa kriteria
    st.sidebar.info("Masukkan beberapa kriteria yang diperlukan")
    alt = st.sidebar.text_input("Enter Nama Calon Nasabah")
    alternatives = alt.split(",")
    st.sidebar.info("Dan masukkan beberapa nama calon nasabah, pisahkan dengan tanda koma tanpa spasi!.")               
    st.sidebar.info("Contoh: Si A,Si B,Si C")


    if cri_options and alt:
        with st.expander("Criteria Weights"):
            st.subheader("Pairwise comparision untuk Kriteria")
            st.write("---")
            n = len(criterias)
            A = np.zeros((n, n))
            Aradio = np.zeros((n,n))
            for i in range(0, n):
                for j in range(i, n):
                    if i == j:
                        A[i][j] = 1
                    else:
                        
                        st.markdown(" ##### Criterion "+criterias[i] + " dibandingkan dengan Criterion " +criterias[j])
                        criteriaradio = st.radio("Pilih kriteria prioritas yang lebih tinggi ",(criterias[i], criterias[j],), horizontal=True)
                        if criteriaradio == criterias[i]:
                            A[i][j] = st.slider(label="Seberapa tinggi "+ criterias[i] +" pada perbandingan dengan "+criterias[j]+ " ?",min_value= 1,max_value= 9,value= 1)
                            A[j][i] = float(1/A[i][j])
                        else:
                            A[j][i] = st.slider(label="Seberapa tinggi "+ criterias[j] +" pada perbandingan dengan "+criterias[i]+ " ?",min_value= 1,max_value= 9,value= 1)
                            A[i][j] = float(1/A[j][i])
                
        with st.expander("Alternative Weights"):
            st.subheader("Pairwise comparison untuk Alternatif")
            m = len(alternatives)
            B = np.zeros((n, m, m))

            for k in range(0, n):
                st.write("---")
                st.markdown(" ##### Perbandingan Alternatif untuk Criterion "+criterias[k])
                for i in range(0, m):
                    for j in range(i, m):
                        if i == j:
                            B[k][i][j] = 1
                        else:
                            alternativeradio = st.radio("Pilih alternatif prioritas yang lebih tinggi untuk kriteria "+criterias[k] ,(alternatives[i], alternatives[j],), horizontal=True)
                            if alternativeradio == alternatives[i]:
                                B[k][i][j] = st.slider("Mempertimbangkan Kriteria " + criterias[k] + ", seberapa tinggi " + alternatives[i] + " dibandingkan dengan " + alternatives[j]+" ?", 1, 9, 1)
                                B[k][j][i] = float(1/B[k][i][j])
                            else:
                                B[k][j][i] = st.slider("Mempertimbangkan Kriteria " + criterias[k] + ", seberapa tinggi " + alternatives[j] + " dibandingkan dengan " + alternatives[i]+" ?", 1, 9, 1)
                                B[k][i][j] = float(1/B[k][j][i])

                
        btn = st.button("Calculate AHP")
        st.write("##")
        if btn:
            calculate_ahp(A, B, n, m, criterias, alternatives)

if __name__ == '__main__':
    main()